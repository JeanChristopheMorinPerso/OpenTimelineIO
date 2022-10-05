// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/any.h"
#include "opentimelineio/version.h"

#include <assert.h>
#include <map>
#include <string>
#include <iostream>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

/**
 * An AnyDictionary has exactly the same API as
 *    std::map<std::string, any>
 *
 * except that it records a "time-stamp" that bumps monotonically every time an
 * operation that would invalidate iterators is performed.
 * (This happens for operator=, clear, erase, insert, swap).  The stamp also
 * lets external observers know when the map has been destroyed (which includes
 * the case of the map being relocated in memory).
 *
 * This allows us to hand out iterators that can be aware of mutation and moves
 * and take steps to safe-guard themselves from causing a crash.  (Yes,
 * I'm talking to you, Python...)
 */
class AnyDictionary : private std::map<std::string, any>
{
public:
    using map::map;

    AnyDictionary()
        : map{}
        , _mutation_stamp{}
    {
        std::cout << "Constructing AnyDictionary\n";
    }

    // to be safe, avoid brace-initialization so as to not trigger
    // list initialization behavior in older compilers:
    AnyDictionary(const AnyDictionary& other)
        : map(other)
        , _mutation_stamp{}
    {
        std::cout << "Constructing AnyDictionary\n";
    }

    ~AnyDictionary()
    {
        std::cout << "Destructing AnyDictionary\n";
        if (_mutation_stamp)
        {
            std::cout << "  There was a mutation\n";
            _mutation_stamp->stamp          = -1;
            _mutation_stamp->any_dictionary = nullptr;
        }
    }

    AnyDictionary& operator=(const AnyDictionary& other)
    {
        mutate();
        map::operator=(other);
        return *this;
    }

    AnyDictionary& operator=(AnyDictionary&& other)
    {
        mutate();
        other.mutate();
        map::operator=(other);
        return *this;
    }

    AnyDictionary& operator=(std::initializer_list<value_type> ilist)
    {
        mutate();
        map::operator=(ilist);
        return *this;
    }

    using map::get_allocator;

    using map::at;
    using map::operator[];

    using map::begin;
    using map::cbegin;
    using map::cend;
    using map::crbegin;
    using map::crend;
    using map::end;
    using map::rbegin;
    using map::rend;

    void clear() noexcept
    {
        mutate();
        map::clear();
    }
    using map::emplace;
    using map::emplace_hint;
    using map::insert;

    iterator erase(const_iterator pos)
    {
        mutate();
        return map::erase(pos);
    }

    iterator erase(const_iterator first, const_iterator last)
    {
        mutate();
        return map::erase(first, last);
    }

    size_type erase(const key_type& key)
    {
        mutate();
        return map::erase(key);
    }

    void swap(AnyDictionary& other)
    {
        mutate();
        other.mutate();
        map::swap(other);
    }

    /// @TODO: remove all of these @{

    // if key is in this, and the type of key matches the type of result, then
    // set result to the value of any_cast<type>(this[key]) and return true,
    // otherwise return false
    template <typename containedType>
    bool get_if_set(const std::string& key, containedType* result) const
    {
        if (result == nullptr)
        {
            return false;
        }

        const auto it = this->find(key);

        if ((it != this->end())
            && (it->second.type().hash_code()
                == typeid(containedType).hash_code()))
        {
            *result = any_cast<containedType>(it->second);
            return true;
        }
        else
        {
            return false;
        }
    }

    inline bool has_key(const std::string& key) const
    {
        return (this->find(key) != this->end());
    }

    // if key is in this, place the value in result and return true, otherwise
    // store the value in result at key and return false
    template <typename containedType>
    bool set_default(const std::string& key, containedType* result)
    {
        if (result == nullptr)
        {
            return false;
        }

        const auto d_it = this->find(key);

        if ((d_it != this->end())
            && (d_it->second.type().hash_code()
                == typeid(containedType).hash_code()))
        {
            *result = any_cast<containedType>(d_it->second);
            return true;
        }
        else
        {
            this->insert({ key, *result });
            return false;
        }
    }

    using map::empty;
    using map::max_size;
    using map::size;

    using map::count;
    using map::equal_range;
    using map::find;
    using map::lower_bound;
    using map::upper_bound;

    using map::key_comp;
    using map::value_comp;

    using map::allocator_type;
    using map::const_iterator;
    using map::const_pointer;
    using map::const_reference;
    using map::const_reverse_iterator;
    using map::difference_type;
    using map::iterator;
    using map::key_compare;
    using map::key_type;
    using map::mapped_type;
    using map::pointer;
    using map::reference;
    using map::reverse_iterator;
    using map::size_type;
    using map::value_type;

    struct MutationStamp
    {
        constexpr MutationStamp(AnyDictionary* d) noexcept
            : stamp{ 1 }
            , any_dictionary{ d }
            , owning{ false }
        {
            assert(d);
        }

        MutationStamp(MutationStamp const&)            = delete;
        MutationStamp& operator=(MutationStamp const&) = delete;

        ~MutationStamp()
        {
            std::cout << "Destructing MutationStamp\n";
            if (any_dictionary)
            {
                std::cout << "  There was an AnyDictionary attached\n";
                any_dictionary->_mutation_stamp = nullptr;
                if (owning)
                {
                    delete any_dictionary;
                }
            }
        }

        int64_t        stamp;
        AnyDictionary* any_dictionary;
        bool           owning;

    protected:
        MutationStamp()
            : stamp{ 1 }
            , any_dictionary{ new AnyDictionary }
            , owning{ true }
        {
            any_dictionary->_mutation_stamp = this;
        }
    };

    MutationStamp* get_or_create_mutation_stamp()
    {
        std::cout << "get_or_create_mutation_stamp\n";
        if (!_mutation_stamp)
        {
            std::cout << "  Creating mutation\n";
            _mutation_stamp = new MutationStamp(this);
        }
        return _mutation_stamp;
    }

    friend struct MutationStamp;

private:
    MutationStamp* _mutation_stamp = nullptr;

    void mutate() noexcept
    {
        if (_mutation_stamp)
        {
            _mutation_stamp->stamp++;
        }
    }
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
